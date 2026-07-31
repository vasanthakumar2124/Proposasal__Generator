import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { billingApi } from '../api/billing'
import { Button } from '../components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Skeleton } from '../components/ui/Skeleton'
import { Check, Loader2, CreditCard, ArrowRight } from 'lucide-react'

const PLAN_FEATURES: Record<string, string[]> = {
  free: ['3 proposals/month', 'HTML exports', 'Basic templates', 'Community support'],
  starter: ['20 proposals/month', 'HTML + PDF exports', 'All templates', 'Email support'],
  professional: ['100 proposals/month', 'All export formats', 'Priority support', 'Advanced analytics', 'Custom branding'],
  enterprise: ['Unlimited proposals', 'All export formats', 'API access', 'Dedicated support', 'Custom branding', 'SSO', 'SLA guarantee'],
}

function PlanCard({
  plan,
  currentPlan,
  onSelect,
  loading,
}: {
  plan: { id: string; name: string; price_monthly: number; price_yearly: number }
  currentPlan?: string
  onSelect: (interval: 'month' | 'year') => void
  loading: boolean
}) {
  const isCurrent = currentPlan === plan.id
  const features = PLAN_FEATURES[plan.id] || []

  return (
    <Card className={`relative flex flex-col ${isCurrent ? 'ring-2 ring-blue-500' : ''}`}>
      {isCurrent && (
        <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600">
          Current Plan
        </Badge>
      )}
      <CardHeader>
        <CardTitle className="text-xl">{plan.name}</CardTitle>
        <CardDescription>{plan.id === 'free' ? 'Get started' : 'For growing teams'}</CardDescription>
      </CardHeader>
      <CardContent className="flex-1">
        <div className="mb-4">
          {plan.price_monthly === 0 ? (
            <span className="text-3xl font-bold">Free</span>
          ) : (
            <>
              <span className="text-3xl font-bold">${plan.price_monthly}</span>
              <span className="text-gray-500 ml-1">/month</span>
            </>
          )}
        </div>
        {plan.price_yearly > 0 && (
          <p className="text-sm text-gray-500 mb-4">${plan.price_yearly}/year (save ${(plan.price_monthly * 12 - plan.price_yearly)})</p>
        )}
        <ul className="space-y-2">
          {features.map((f) => (
            <li key={f} className="flex items-center gap-2 text-sm">
              <Check className="h-4 w-4 text-green-500 flex-shrink-0" />
              {f}
            </li>
          ))}
        </ul>
      </CardContent>
      <CardFooter>
        {plan.id === 'free' ? (
          <Button variant="outline" className="w-full" disabled={isCurrent}>
            {isCurrent ? 'Active' : 'Downgrade'}
          </Button>
        ) : (
          <Button
            className="w-full"
            variant={isCurrent ? 'outline' : 'default'}
            disabled={loading}
            onClick={() => onSelect(isCurrent ? 'year' : 'month')}
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
            {isCurrent ? 'Manage' : `Choose ${plan.name}`}
          </Button>
        )}
      </CardFooter>
    </Card>
  )
}

export default function BillingPage() {
  const [interval, setInterval] = useState<'month' | 'year'>('month')

  const { data: plansData } = useQuery({
    queryKey: ['billing-plans'],
    queryFn: () => billingApi.getPlans(),
  })

  const { data: subData, isLoading: subLoading } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => billingApi.getSubscription(),
  })

  const checkout = useMutation({
    mutationFn: (planId: string) => billingApi.createCheckout(planId, interval),
    onSuccess: (data) => {
      const url = data.data?.url || data.data?.data?.url
      if (url) window.location.href = url
    },
  })

  const plans = plansData?.data?.plans || plansData?.data?.data?.plans || []
  const subscription = subData?.data?.plan_id || subData?.data?.data?.plan_id || 'free'

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Billing & Plans</h1>
          <p className="text-gray-500">Choose the right plan for your team</p>
        </div>
        <Button variant="outline" onClick={() => billingApi.getPortalUrl().then(r => {
          const url = r.data?.url || r.data?.data?.url
          if (url) window.location.href = url
        })}>
          <CreditCard className="h-4 w-4 mr-2" /> Billing Portal
        </Button>
      </div>

      <div className="flex gap-2 justify-center">
        <Button
          variant={interval === 'month' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setInterval('month')}
        >Monthly</Button>
        <Button
          variant={interval === 'year' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setInterval('year')}
        >Annual <Badge variant="secondary" className="ml-1">Save ~17%</Badge></Button>
      </div>

      {subLoading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-80" />)}
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {plans.map((plan: { id: string; name: string; price_monthly: number; price_yearly: number }) => (
            <PlanCard
              key={plan.id}
              plan={plan}
              currentPlan={subscription}
              onSelect={() => checkout.mutate(plan.id)}
              loading={checkout.isPending}
            />
          ))}
        </div>
      )}
    </div>
  )
}
