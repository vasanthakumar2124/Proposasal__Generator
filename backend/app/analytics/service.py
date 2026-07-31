import logging
from datetime import datetime, timedelta, timezone

from app.database.mongodb import db

logger = logging.getLogger("proposalcraft.analytics")


class AnalyticsService:
    async def get_org_dashboard(self, org_id: str) -> dict:
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        total_proposals = await db.proposals.count_documents({"organization_id": org_id})
        recent_proposals = await db.proposals.count_documents({
            "organization_id": org_id,
            "created_at": {"$gte": thirty_days_ago},
        })
        total_clients = await db.clients.count_documents({"organization_id": org_id})
        total_projects = await db.projects.count_documents({"organization_id": org_id})
        total_workspaces = await db.workspaces.count_documents({"organization_id": org_id})

        sub = await db.subscriptions.find_one(
            {"organization_id": org_id, "status": {"$in": ["active", "trialing"]}},
        )

        proposals_by_status = await db.proposals.aggregate([
            {"$match": {"organization_id": org_id}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]).to_list(None)

        recent = await db.proposals.find(
            {"organization_id": org_id},
        ).sort("created_at", -1).limit(5).to_list(5)
        for r in recent:
            r["_id"] = str(r["_id"])

        projects = await db.projects.find(
            {"organization_id": org_id},
        ).sort("created_at", -1).to_list(None)
        for p in projects:
            p["_id"] = str(p["_id"])

        clients = await db.clients.find(
            {"organization_id": org_id},
        ).sort("created_at", -1).to_list(None)
        for c in clients:
            c["_id"] = str(c["_id"])

        return {
            "stats": {
                "total_proposals": total_proposals,
                "recent_proposals_30d": recent_proposals,
                "total_clients": total_clients,
                "total_projects": total_projects,
                "total_workspaces": total_workspaces,
                "plan": sub["plan_id"] if sub else "free",
            },
            "proposals_by_status": {s["_id"] or "draft": s["count"] for s in proposals_by_status},
            "recent_proposals": [
                {"id": r["_id"], "title": r.get("title", ""), "status": r.get("status", "draft")}
                for r in recent
            ],
            "recent_projects": [
                {"id": p["_id"], "name": p.get("name", ""), "status": p.get("status", "active")}
                for p in projects[:5]
            ],
            "recent_clients": [
                {"id": c["_id"], "name": c.get("name", ""), "industry": c.get("industry", "")}
                for c in clients[:5]
            ],
        }

    async def get_admin_dashboard(self) -> dict:
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        total_orgs = await db.organizations.count_documents({})
        total_users = await db.users.count_documents({})
        total_proposals = await db.proposals.count_documents({})
        recent_signups = await db.users.count_documents({
            "created_at": {"$gte": thirty_days_ago},
        })
        active_subs = await db.subscriptions.count_documents({
            "status": {"$in": ["active", "trialing"]},
        })
        revenue = await db.subscriptions.aggregate([
            {"$match": {"status": "active"}},
            {"$lookup": {"from": "plans", "localField": "plan_id", "foreignField": "id", "as": "plan"}},
            {"$unwind": {"path": "$plan", "preserveNullAndEmptyArrays": True}},
            {"$group": {"_id": None, "total": {"$sum": "$plan.price_monthly"}}},
        ]).to_list(1)
        monthly_revenue = revenue[0]["total"] if revenue else 0

        proposals_by_day = await db.proposals.aggregate([
            {"$match": {"created_at": {"$gte": thirty_days_ago}}},
            {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}, "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]).to_list(None)

        return {
            "stats": {
                "total_organizations": total_orgs,
                "total_users": total_users,
                "total_proposals": total_proposals,
                "active_subscriptions": active_subs,
                "monthly_revenue": monthly_revenue,
                "recent_signups_30d": recent_signups,
            },
            "proposals_by_day": {d["_id"]: d["count"] for d in proposals_by_day},
            "timestamp": now.isoformat(),
        }


analytics_service = AnalyticsService()
