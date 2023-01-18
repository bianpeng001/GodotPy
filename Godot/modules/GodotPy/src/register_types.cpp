#include "../register_types.h"
#include "core/object/class_db.h"

#include "GodotPy.h"
#include "fiolina.h"

void initialize_fiolina_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
            return;
    }
	FLibPy::Init();
	ClassDB::register_class<FPyModule>();
	ClassDB::register_class<FObject>();
}

void uninitialize_fiolina_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
            return;
    }
}
