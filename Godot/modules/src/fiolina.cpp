//
// 2023年1月11日
//
#include "fiolina.h"

#include "core/os/os.h"

FioStart::FioStart() {
	
}

FioStart::~FioStart() {
}

void FioStart::_ready() {
	print_line("FioStart::_ready");
}

void FioStart::_notification(int p_what) {
	//print_line(vformat("FioStart::_notification %d", p_what));
	switch (p_what) {
		case NOTIFICATION_READY:
			_ready();
			break;
	}
}

void FioStart::_bind_methods() {
	const char class_name[] = "FioStart";
	ClassDB::bind_static_method(class_name, D_METHOD("say_hello"), &FioStart::say_hello);
}

void FioStart::say_hello() {
	print_line("hello");
}

