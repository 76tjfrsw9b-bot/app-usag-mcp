import os  
from datetime import datetime  
from typing import Optional  
from mcp.server.fastmcp import FastMCP  
from supabase import create_client, Client  
  
# **初始化** Supabase **客户端**  
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://jgsxbcsdijbkgymjdzyf.supabase.co")  
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_peSJTn97MO2zmRLr1Lwdyw_8VO12v32")  
  
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)  
  
# **创建** MCP **服务**  
mcp = FastMCP("app-usage-tracker")  
  
  
@mcp.tool()  
def query_app_usage(  
    app_name: Optional**[**str**]** = None,  
    start_time: Optional**[**str**]** = None,  
    end_time: Optional**[**str**]** = None  
) -> dict:  
    """  
    **查询** App **使用记录**  
      
    **参数**:  
    - app_name: **可选，**App **名称（如** "**抖音**"**、**"**小红书**"**）**  
    - start_time: **可选，开始时间（格式：**2026-08-24 00:00:00**）**  
    - end_time: **可选，结束时间（格式：**2026-08-24 23:59:59**）**  
      
    **返回**:  
    - **使用记录列表，包含每个** App **的打开次数和时间**  
    """  
    query = supabase.table("app_usage").select("*")  
      
    if app_name:  
        query = query.eq("app_name", app_name)  
      
    if start_time:  
        query = query.gte("created_at", start_time)  
      
    if end_time:  
        query = query.lte("created_at", end_time)  
      
    query = query.order("created_at", desc=True)  
      
    result = query.execute()  
      
    # **统计每个** App **的使用次数**  
    app_counts = {}  
    for record in result.data:  
        name = record.get("app_name", "**未知**")  
        if name not in app_counts:  
            app_counts**[**name**]** = {"count": 0, "records": **[]**}  
        app_counts**[**name**][**"count"**]** += 1  
        app_counts**[**name**][**"records"**]**.append({  
            "action": record.get("action"),  
            "time": record.get("created_at")  
        })  
      
    return {  
        "total_records": len(result.data),  
        "app_summary": app_counts,  
        "raw_data": result.data  
    }  
  
  
@mcp.tool()  
def get_today_usage() -> dict:  
    """  
    **获取今天的** App **使用情况汇总**  
      
    **返回**:  
    - **今天所有** App **的使用次数统计**  
    """  
    today = datetime.now().strftime("%Y-%m-%d")  
    start_time = f"{today} 00:00:00"  
    end_time = f"{today} 23:59:59"  
      
    return query_app_usage(start_time=start_time, end_time=end_time)  
  
  
@mcp.tool()  
def get_app_stats(app_name: str) -> dict:  
    """  
    **获取指定** App **的使用统计**  
      
    **参数**:  
    - app_name: App **名称（如** "**抖音**"**）**  
      
    **返回**:  
    - **该** App **的总使用次数、最近使用时间等**  
    """  
    result = query_app_usage(app_name=app_name)  
      
    if result**[**"total_records"**]** == 0:  
        return {"message": f"**没有找到** {app_name} **的使用记录**"}  
      
    records = result**[**"raw_data"**]**  
      
    return {  
        "app_name": app_name,  
        "total_opens": result**[**"total_records"**]**,  
        "last_used": records**[**0**][**"created_at"**]** if records else None,  
        "first_used": records**[**-1**][**"created_at"**]** if records else None  
    }  
  
  
if __name__ == "__main__":  
    mcp.run()  
