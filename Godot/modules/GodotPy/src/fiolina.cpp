//
// 2023年1月11日
//
#include "fiolina.h"

#include "core/os/os.h"

FObject::FObject() {
	
}

FObject::~FObject() {
}

void FObject::_ready() {
	print_line("FObject::_ready");
}

void FObject::_notification(int p_what) {
	//print_line(vformat("FioStart::_notification %d", p_what));
	switch (p_what) {
		case NOTIFICATION_READY:
			_ready();
			break;
	}
}

void FObject::_bind_methods() {
	const char class_name[] = "FObject";
	ClassDB::bind_static_method(class_name, D_METHOD("say_hello"), &FObject::say_hello);
}

void FObject::say_hello() {
	print_line("hello");
}

