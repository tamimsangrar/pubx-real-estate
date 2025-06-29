import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface Lead {
  id: string
  name: string
  email: string
  phone: string | null
  source: string
  created_at: string
}

interface LeadScore {
  lead_id: string
  score: number
  reason: string
}

// Rule-based scoring function
function calculateLeadScore(lead: Lead): { score: number; reason: string } {
  let score = 0
  const reasons: string[] = []

  // Check email domain (not temp mail)
  const emailDomain = lead.email.split('@')[1]?.toLowerCase()
  const tempMailDomains = ['tempmail.com', 'temp-mail.org', '10minutemail.com', 'guerrillamail.com']
  
  if (emailDomain && !tempMailDomains.includes(emailDomain)) {
    score += 20
    reasons.push('Valid email domain')
  }

  // Check phone number (E.164 format)
  if (lead.phone && /^\+[1-9]\d{1,14}$/.test(lead.phone)) {
    score += 30
    reasons.push('Verified phone number')
  }

  // Check if lead has name (basic validation)
  if (lead.name && lead.name.trim().length > 2) {
    score += 10
    reasons.push('Valid name provided')
  }

  // Check source quality
  if (lead.source === 'chat') {
    score += 10
    reasons.push('Engaged via chat')
  } else if (lead.source === 'voice') {
    score += 20
    reasons.push('Engaged via voice call')
  }

  // Additional scoring based on engagement time
  const createdAt = new Date(lead.created_at)
  const now = new Date()
  const hoursSinceCreation = (now.getTime() - createdAt.getTime()) / (1000 * 60 * 60)
  
  if (hoursSinceCreation < 24) {
    score += 10
    reasons.push('Recent engagement')
  }

  return {
    score: Math.min(score, 100), // Cap at 100
    reason: reasons.join(', ')
  }
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Initialize Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    
    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    // Get leads without scores
    const { data: leadsWithoutScores, error: fetchError } = await supabase
      .from('leads')
      .select('id, name, email, phone, source, created_at')
      .not('id', 'in', `(
        SELECT lead_id FROM lead_scores
      )`)

    if (fetchError) {
      console.error('Error fetching leads:', fetchError)
      return new Response(
        JSON.stringify({ error: 'Failed to fetch leads' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (!leadsWithoutScores || leadsWithoutScores.length === 0) {
      return new Response(
        JSON.stringify({ message: 'No new leads to score' }),
        { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Calculate scores for each lead
    const scoresToInsert: LeadScore[] = []
    const highScoreLeads: string[] = []

    for (const lead of leadsWithoutScores) {
      const { score, reason } = calculateLeadScore(lead)
      
      scoresToInsert.push({
        lead_id: lead.id,
        score,
        reason
      })

      // Check if score meets threshold for notification
      const threshold = 70 // This could be fetched from settings table
      if (score >= threshold) {
        highScoreLeads.push(lead.id)
      }
    }

    // Insert scores in batch
    const { error: insertError } = await supabase
      .from('lead_scores')
      .insert(scoresToInsert)

    if (insertError) {
      console.error('Error inserting scores:', insertError)
      return new Response(
        JSON.stringify({ error: 'Failed to insert scores' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Notify chat orchestrator about high-score leads via Realtime
    if (highScoreLeads.length > 0) {
      const { error: notifyError } = await supabase
        .channel('lead-scoring')
        .send({
          type: 'broadcast',
          event: 'high-score-lead',
          payload: { lead_ids: highScoreLeads }
        })

      if (notifyError) {
        console.error('Error notifying about high-score leads:', notifyError)
      }
    }

    return new Response(
      JSON.stringify({
        message: `Scored ${scoresToInsert.length} leads`,
        high_score_count: highScoreLeads.length,
        scores: scoresToInsert
      }),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Unexpected error:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
}) 