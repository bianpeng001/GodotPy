//
// 2023年1月11日
//
#pragma once

#include "scene/main/node.h"

/// <summary>
/// 启动逻辑
/// </summary>
class FObject : public Node {
	GDCLASS(FObject, Node);

private:
	// 在GDCLASS的机制，如果定义了_notification(int）
	// 就会在这里处理notification
	void _notification(int p_what);
	void _ready();

protected:
	static void _bind_methods();
	
public:
	FObject();
	virtual ~FObject();
	static void say_hello();

};
