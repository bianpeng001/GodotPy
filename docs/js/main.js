
import {javascriptGenerator} from 'javascript'
import {pythonGenerator} from 'python'
import {luaGenerator} from 'lua'

function init_blockly() {
    var toolbox = {
        "kind": "flyoutToolbox",
        "contents": [
        {
        "kind": "block",
        "type": "controls_if"
        },
        {
        "kind": "block",
        "type": "controls_repeat_ext"
        },
        {
        "kind": "block",
        "type": "logic_compare"
        },
        {
        "kind": "block",
        "type": "math_number"
        },
        {
        "kind": "block",
        "type": "math_arithmetic"
        },
        {
        "kind": "block",
        "type": "text"
        },
        {
        "kind": "block",
        "type": "text_print"
        },
        ]
    }
    var workspace = Blockly.inject('blocklyDiv', {toolbox: toolbox});
}

$(document).ready(() => {
    console.log('ready')

    init_blockly();
})
