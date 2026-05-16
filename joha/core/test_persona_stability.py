"""
人设稳定性改进测试脚本
测试所有5个改进点
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from joha.core.response_postprocessor import post_processor
from joha.core.persona_monitor import persona_monitor


def test_thinking_content_filter():
    """测试1: 过滤思考内容"""
    print("=" * 60)
    print("测试1: 过滤思考内容")
    print("=" * 60)
    
    test_cases = [
        "嗯，好的",
        "（对方说都十二点多了，明天还有早八，看来是真的很晚了）嗯 睡吧",
        "行吧（估计他困了）",
        "知道了（对话结束，无需继续）",
    ]
    
    for original in test_cases:
        processed = post_processor.process(original)
        status = "✅" if processed != original else "⚪"
        print(f"{status} 原: {original}")
        print(f"   新: {processed}")
        print()


def test_other_persona_filter():
    """测试2: 过滤其他人格"""
    print("=" * 60)
    print("测试2: 过滤其他人格")
    print("=" * 60)
    
    test_cases = [
        "好嘞好嘞～收到指令！小伊伊已准备就绪",
        "今天也要元气满满地陪大家聊天哦！✨😊",
        "正常的回复",
    ]
    
    for original in test_cases:
        processed = post_processor.process(original)
        status = "✅" if processed != original else "⚪"
        print(f"{status} 原: {original[:50]}")
        print(f"   新: {processed}")
        print()


def test_meta_cognitive_filter():
    """测试3: 过滤元认知内容"""
    print("=" * 60)
    print("测试3: 过滤元认知内容")
    print("=" * 60)
    
    test_cases = [
        "作为大学生，我觉得应该早点睡",
        "我需要表达一下关心",
        "我要表达我的想法",
        "正常的关心话语",
    ]
    
    for original in test_cases:
        processed = post_processor.process(original)
        status = "✅" if processed != original else "⚪"
        print(f"{status} 原: {original}")
        print(f"   新: {processed}")
        print()


def test_response_diversity():
    """测试4: 回复多样性"""
    print("=" * 60)
    print("测试4: 回复多样性（连续获取备用回复）")
    print("=" * 60)
    
    # 重置状态
    post_processor.last_fallback = None
    
    responses = []
    for i in range(10):
        response = post_processor._get_fallback_response('neutral')
        responses.append(response)
        print(f"{i+1}. {response}")
    
    # 检查是否有重复
    unique_count = len(set(responses))
    print(f"\n唯一回复数: {unique_count}/10")
    if unique_count > 5:
        print("✅ 多样性良好")
    else:
        print("⚠️ 多样性不足")
    print()


def test_persona_monitor():
    """测试5: 人设监控器"""
    print("=" * 60)
    print("测试5: 人设监控器")
    print("=" * 60)
    
    # 模拟一些回复
    test_responses = [
        ("嗯，好的", "嗯，好的", False),
        ("（思考中）嗯", "嗯", True),
        ("小伊伊来了", "嗯", True),
        ("哈哈", "哈哈", False),
        ("知道了", "知道了", False),
    ]
    
    for original, processed, filtered in test_responses:
        persona_monitor.record_response(original, processed, filtered)
    
    # 生成报告
    report = persona_monitor.format_report()
    print(report)
    print()
    
    # 检查警告
    alerts = persona_monitor.check_and_alert()
    if alerts:
        print("⚠️ 警告信息:")
        for alert in alerts:
            print(f"  {alert}")
    else:
        print("✅ 无警告")
    print()


def main():
    print("\n🧪 Joha人设稳定性改进测试\n")
    
    try:
        test_thinking_content_filter()
        test_other_persona_filter()
        test_meta_cognitive_filter()
        test_response_diversity()
        test_persona_monitor()
        
        print("=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
