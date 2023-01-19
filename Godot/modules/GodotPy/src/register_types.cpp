#include "../register_types.h"
#include "core/object/class_db.h"

#include "GodotPy.h"
#include "fiolina.h"

void initialize_GodotPy_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
            return;
    }
	FLibPy::Init();
	ClassDB::register_class<FPyObject>();
	ClassDB::register_class<FObject>();
}

void uninitialize_GodotPy_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
            return;
    }
}
