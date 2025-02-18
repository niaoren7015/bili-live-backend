# app.py （全功能修复版）
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化应用
app = Flask(__name__)
CORS(app)  # 启用CORS

# 健康检查端点（Render必备） ✅
@app.route('/')
def health_check():
    logger.info("收到健康检查请求")
    return jsonify({"status": "ok", "message": "服务运行中"}), 200

# 处理Vercel的接口请求 ✅
@app.route('/start', methods=['POST'])
def handle_start():
    try:
        # 参数验证
        data = request.get_json()
        if not data or 'code' not in data:
            logger.error("收到无效请求：缺少code参数")
            return jsonify(
                {"error": "Missing required parameter: code"}
            ), 400

        code = data['code']
        logger.info(f"处理身份码：{code[:3]}****")  # 安全日志记录

        # TODO: 在此处添加您的业务验证逻辑，例如调用B站API
        # dummy_response = requests.post(bili_api_url, json={...})

        return jsonify({
            "success": True,
            "data": {
                "game_id": "demo_12345",
                "wss_link": "wss://example.com" 
            }
        }), 200

    except Exception as e:
        logger.error(f"处理请求时发生异常：{str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500

# Render端口动态绑定（关键配置） ✅
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # 必须使用环境变量PORT
    app.run(host='0.0.0.0', port=port)
