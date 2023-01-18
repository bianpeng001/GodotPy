#include "../register_types.h"
#include "core/object/class_db.h"

#include "fiolina.h"
#include "libpython.h"

void initialize_fiolina_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
            return;
    }
	FioLibPython::Init();
	ClassDB::register_class<FioExecPython>();
	ClassDB::register_class<FioStart>();
}

void uninitialize_fiolina_module(ModuleInitializationLevel p_level) {
    if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
            return;
    }
}
