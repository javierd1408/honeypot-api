from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models import IntrusionLog
from app.security.auth import verify_admin_token

# Require the admin token for all routes in this router
router = APIRouter(dependencies=[Depends(verify_admin_token)])

@router.get("/intruders")
async def get_intruders_summary(db: AsyncSession = Depends(get_db)):
    """
    Returns a summary of the captured attacks.
    """
    
    # 1. Get Top Attacking IPs
    top_ips_query = (
        select(IntrusionLog.ip_address, func.count(IntrusionLog.id).label("attack_count"))
        .group_by(IntrusionLog.ip_address)
        .order_by(desc("attack_count"))
        .limit(10)
    )
    result_ips = await db.execute(top_ips_query)
    top_ips = [{"ip": row.ip_address, "count": row.attack_count} for row in result_ips.fetchall()]

    # 2. Get Threat Types Breakdown
    threats_query = (
        select(IntrusionLog.threat_type, func.count(IntrusionLog.id).label("count"))
        .group_by(IntrusionLog.threat_type)
        .order_by(desc("count"))
    )
    result_threats = await db.execute(threats_query)
    threat_types = [{"type": row.threat_type, "count": row.count} for row in result_threats.fetchall()]

    # 3. Total attacks logged
    total_query = select(func.count(IntrusionLog.id))
    result_total = await db.execute(total_query)
    total_attacks = result_total.scalar_one()

    return {
        "status": "success",
        "data": {
            "total_attacks_logged": total_attacks,
            "top_attacking_ips": top_ips,
            "frequent_threat_types": threat_types
        }
    }

@router.get("/intruders/logs")
async def get_raw_logs(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """
    Returns the raw logs, paginated.
    """
    query = select(IntrusionLog).order_by(desc(IntrusionLog.timestamp)).limit(limit).offset(offset)
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return {
        "status": "success",
        "data": logs
    }
