"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
var vscode = require("vscode");
var fs = require("fs");
var path = require("path");
var child_process = require("child_process");
var CommandItem = /** @class */ (function (_super) {
    __extends(CommandItem, _super);
    function CommandItem(label, commandId, icon, context) {
        var _this = _super.call(this, label, vscode.TreeItemCollapsibleState.None) || this;
        _this.label = label;
        _this.commandId = commandId;
        _this.icon = icon;
        _this.context = context;
        _this.command = {
            command: commandId,
            title: _this.label,
        };
        if (icon) {
            _this.iconPath = {
                light: path.join(context.extensionPath, 'images', 'light', icon),
                dark: path.join(context.extensionPath, 'images', 'dark', icon)
            };
        }
        return _this;
    }
    return CommandItem;
}(vscode.TreeItem));
var CommandTreeDataProvider = /** @class */ (function () {
    function CommandTreeDataProvider(items) {
        this.items = items;
    }
    CommandTreeDataProvider.prototype.getTreeItem = function (element) {
        return element;
    };
    CommandTreeDataProvider.prototype.getChildren = function (element) {
        if (element === undefined) {
            return Promise.resolve(this.items);
        }
        return Promise.resolve([]);
    };
    return CommandTreeDataProvider;
}());
function createCommandPanel(context) {
    var extension = vscode.extensions.getExtension('UniversalDevices.iox-plugin-ext');
    if (!extension) {
        console.error('Extension not found.');
        return;
    }
    var commands = extension.packageJSON.contributes.commands;
    if (!commands) {
        console.error('Commands not found in packageJSON.');
        return;
    }
    var commandItems = commands.map(function (cmd) { return new CommandItem(cmd.title, cmd.command, cmd.icon, context); });
    var treeDataProvider = new CommandTreeDataProvider(commandItems);
    vscode.window.createTreeView('ioxPluginSidebar', { treeDataProvider: treeDataProvider });
    /* context.subscriptions.push(
         vscode.commands.registerCommand('myExtension.command1', () => {
             vscode.window.showInformationMessage('Command 1 executed!');
         }),
         vscode.commands.registerCommand('myExtension.command2', () => {
             vscode.window.showInformationMessage('Command 2 executed!');
         })
     );*/
}
function checkAndInstallPythonModules() {
    return __awaiter(this, void 0, void 0, function () {
        var pythonInterpreter, modules;
        return __generator(this, function (_a) {
            pythonInterpreter = vscode.workspace.getConfiguration('python3').get('pythonPath', 'pip3');
            modules = ['astor', 'ioxplugin', 'fastjsonschema'];
            modules.forEach(function (module) {
                child_process.exec("".concat(pythonInterpreter, " -c \"import ").concat(module, "\""), function (error, stdout, stderr) {
                    if (error) {
                        vscode.window.showInformationMessage("".concat(module, " is not installed. Installing..."));
                        child_process.exec("".concat(pythonInterpreter, " install ").concat(module), function (installError, installStdout, installStderr) {
                            if (installError) {
                                vscode.window.showErrorMessage("Failed to install ".concat(module, ": ").concat(installStderr));
                            }
                            else {
                                vscode.window.showInformationMessage("".concat(module, " installed successfully."));
                            }
                        });
                    }
                });
            });
            return [2 /*return*/];
        });
    });
}
function createNewIoXPluginProject(context) {
    return __awaiter(this, void 0, void 0, function () {
        var workspaceFolder_1, scriptPath, pythonProcess, error_1, message;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, vscode.window.showInputBox({
                            prompt: 'Enter path for the new IoX Plugin project',
                            value: vscode.workspace.workspaceFolders == undefined ? "type path here" : vscode.workspace.workspaceFolders[0].uri.fsPath
                        })];
                case 1:
                    workspaceFolder_1 = _a.sent();
                    if (!workspaceFolder_1) {
                        vscode.window.showErrorMessage('Project creation cancelled.');
                        return [2 /*return*/, false];
                    }
                    scriptPath = path.join(context.extensionPath, 'code', 'new_project.py');
                    pythonProcess = child_process.spawn('python3', [scriptPath, workspaceFolder_1, context.extensionPath]);
                    pythonProcess.stdout.on('data', function (data) {
                        console.log("".concat(data));
                        vscode.window.showInformationMessage("".concat(data));
                    });
                    pythonProcess.stderr.on('data', function (data) {
                        console.error("".concat(data));
                        vscode.window.showErrorMessage("".concat(data));
                    });
                    pythonProcess.on('close', function (code) {
                        if (code !== 0) {
                            console.log("".concat(code));
                            vscode.window.showErrorMessage("".concat(code));
                            return false;
                        }
                        else {
                            console.log('Generating IoX Plugin project completed successfully');
                            vscode.window.showInformationMessage('Generating IoX Plugin project completed successfully');
                            var uri = vscode.Uri.file(workspaceFolder_1);
                            vscode.commands.executeCommand('vscode.openFolder', uri, false);
                        }
                    });
                    return [3 /*break*/, 3];
                case 2:
                    error_1 = _a.sent();
                    if (typeof error_1 === "object" && error_1 !== null && "message" in error_1) {
                        message = error_1.message;
                        vscode.window.showErrorMessage("Failed to create project: ".concat(message));
                    }
                    else {
                        vscode.window.showErrorMessage("Failed to create project due to an unknown error");
                    }
                    return [2 /*return*/, false];
                case 3:
                    vscode.window.showInformationMessage('Generating IoX Plugin project completed successfully');
                    return [2 /*return*/, true];
            }
        });
    });
}
function createJSON(context) {
    return __awaiter(this, void 0, void 0, function () {
        var packageJsonPath, packageJsonContent, packageJson, snippetOptions, pickedSnippet, workspaceFolders, destinationPath, error_2, message;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    packageJsonPath = path.join(context.extensionPath, 'package.json');
                    packageJsonContent = fs.readFileSync(packageJsonPath, 'utf8');
                    packageJson = JSON.parse(packageJsonContent);
                    snippetOptions = packageJson.contributes.snippets.map(function (snippet) { return ({
                        label: snippet.description,
                        detail: snippet.path,
                        fullPath: path.join(context.extensionPath, snippet.path)
                    }); });
                    return [4 /*yield*/, vscode.window.showQuickPick(snippetOptions, {
                            placeHolder: 'Please choose a template ...'
                        })];
                case 1:
                    pickedSnippet = _a.sent();
                    if (pickedSnippet) {
                        workspaceFolders = vscode.workspace.workspaceFolders;
                        if (workspaceFolders) {
                            destinationPath = path.join(workspaceFolders[0].uri.fsPath, path.basename(pickedSnippet.fullPath));
                            fs.copyFileSync(pickedSnippet.fullPath, destinationPath);
                            vscode.window.showInformationMessage("Template copied to ".concat(destinationPath));
                            vscode.commands.executeCommand('workbench.action.focusSideBar');
                            vscode.commands.executeCommand('workbench.view.explorer');
                        }
                    }
                    return [3 /*break*/, 3];
                case 2:
                    error_2 = _a.sent();
                    if (typeof error_2 === "object" && error_2 !== null && "message" in error_2) {
                        message = error_2.message;
                        vscode.window.showErrorMessage("Failed to copy template: ".concat(message));
                    }
                    else {
                        vscode.window.showErrorMessage("Failed to copy template due to an unknown error");
                    }
                    return [2 /*return*/, false];
                case 3: return [2 /*return*/, true];
            }
        });
    });
}
function getPluginJSONFile(context) {
    return __awaiter(this, void 0, void 0, function () {
        var fileExtension, workspaceFolder, pattern, files, items, error_3, message;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    fileExtension = '.iox_plugin.json';
                    if (!vscode.workspace.workspaceFolders) {
                        vscode.window.showErrorMessage('No open workspace. Please open a directory first.');
                        return [2 /*return*/, null];
                    }
                    workspaceFolder = vscode.workspace.workspaceFolders[0].uri.fsPath;
                    pattern = new vscode.RelativePattern(workspaceFolder, "**/*".concat(fileExtension));
                    return [4 /*yield*/, vscode.workspace.findFiles(pattern, null, 1)];
                case 1:
                    files = _a.sent();
                    if (files.length === 0) {
                        vscode.window.showErrorMessage("You don't have any IoX Plugin JSON Files. Let's create one!");
                        createJSON(context);
                    }
                    else {
                        items = files.map(function (file) { return ({
                            detail: file.fsPath,
                            uri: file
                        }); });
                        vscode.window.showInformationMessage("Generating Plugin Code for ".concat(items[0].detail, "."));
                        return [2 /*return*/, items[0].uri];
                    }
                    return [3 /*break*/, 3];
                case 2:
                    error_3 = _a.sent();
                    if (typeof error_3 === "object" && error_3 !== null && "message" in error_3) {
                        message = error_3.message;
                        vscode.window.showErrorMessage("Failed to copy template: ".concat(message));
                    }
                    else {
                        vscode.window.showErrorMessage("Failed to copy template due to an unknown error");
                    }
                    return [2 /*return*/, null];
                case 3: return [2 /*return*/, null];
            }
        });
    });
}
function generatePluginCode(context, fileUri) {
    return __awaiter(this, void 0, void 0, function () {
        var workspaceFolder, scriptPath, fu, pythonPath, pythonProcess, error_4, message;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 3, , 4]);
                    workspaceFolder = vscode.workspace.workspaceFolders == undefined ? "type path here" : vscode.workspace.workspaceFolders[0].uri.fsPath;
                    if (!workspaceFolder) {
                        vscode.window.showErrorMessage('Cannot find project directory');
                        return [2 /*return*/, false];
                    }
                    scriptPath = path.join(context.extensionPath, 'code', 'plugin.py');
                    if (!!fileUri) return [3 /*break*/, 2];
                    return [4 /*yield*/, getPluginJSONFile(context)];
                case 1:
                    fu = _a.sent();
                    fileUri = fu;
                    _a.label = 2;
                case 2:
                    if (!fileUri)
                        return [2 /*return*/, false];
                    pythonPath = context.extensionPath;
                    pythonProcess = child_process.spawn('python3', [scriptPath, workspaceFolder, fileUri.fsPath]);
                    pythonProcess.stdout.on('data', function (data) {
                        console.log("".concat(data));
                        vscode.window.showInformationMessage("".concat(data));
                    });
                    pythonProcess.stderr.on('data', function (data) {
                        console.error("".concat(data));
                        vscode.window.showErrorMessage("".concat(data));
                    });
                    pythonProcess.on('close', function (code) {
                        if (code !== 0) {
                            console.log("IoX Plugin Code generation exited with code ".concat(code));
                            vscode.window.showErrorMessage("IoX Plugin Code generation exited with code ".concat(code));
                            return false;
                        }
                        else {
                            console.log('IoX Plugin Code generation completed successfully');
                            vscode.window.showInformationMessage('IoX Plugin Code generation completed successfully');
                            vscode.commands.executeCommand('workbench.action.focusSideBar');
                            vscode.commands.executeCommand('workbench.view.explorer');
                        }
                    });
                    return [3 /*break*/, 4];
                case 3:
                    error_4 = _a.sent();
                    if (typeof error_4 === "object" && error_4 !== null && "message" in error_4) {
                        message = error_4.message;
                        vscode.window.showErrorMessage("Failed to generated IoX Plugin Code: ".concat(message));
                    }
                    else {
                        vscode.window.showErrorMessage("Failed to generated IoX Plugin Code due to an unknown error");
                    }
                    return [2 /*return*/, false];
                case 4:
                    vscode.window.showInformationMessage('IoX Plugin Code generation completed successfully');
                    return [2 /*return*/, true];
            }
        });
    });
}
function activate(context) {
    var _this = this;
    var python_dep = vscode.commands.registerCommand('iox-plugin-ext.ensurePythonDependencies', function () { return __awaiter(_this, void 0, void 0, function () {
        return __generator(this, function (_a) {
            checkAndInstallPythonModules();
            return [2 /*return*/];
        });
    }); });
    context.subscriptions.push(python_dep);
    checkAndInstallPythonModules();
    var createProject = vscode.commands.registerCommand('iox-plugin-ext.createProject', function () { return __awaiter(_this, void 0, void 0, function () {
        var prc;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, createNewIoXPluginProject(context)];
                case 1:
                    prc = _a.sent();
                    if (prc.valueOf())
                        context.subscriptions.push(createProject);
                    return [2 /*return*/];
            }
        });
    }); });
    var create_JSON = vscode.commands.registerCommand('iox-plugin-ext.createJSON', function (fileUri) { return __awaiter(_this, void 0, void 0, function () {
        var prc;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, createJSON(context)];
                case 1:
                    prc = _a.sent();
                    if (prc.valueOf())
                        context.subscriptions.push(create_JSON);
                    return [2 /*return*/];
            }
        });
    }); });
    var generateCode = vscode.commands.registerCommand('iox-plugin-ext.generatePluginCode', function (fileUri) { return __awaiter(_this, void 0, void 0, function () {
        var prc;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, generatePluginCode(context, fileUri)];
                case 1:
                    prc = _a.sent();
                    if (prc.valueOf())
                        context.subscriptions.push(generateCode);
                    return [2 /*return*/];
            }
        });
    }); });
    createCommandPanel(context);
}
exports.activate = activate;
function deactivate() { }
exports.deactivate = deactivate;
