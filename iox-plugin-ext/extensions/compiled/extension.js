"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const child_process = __importStar(require("child_process"));
function checkAndInstallPythonModules() {
    return __awaiter(this, void 0, void 0, function* () {
        const pythonInterpreter = vscode.workspace.getConfiguration('python3').get('pythonPath', 'pip3');
        const modules = ['astor']; // Example modules
        modules.forEach(module => {
            child_process.exec(`${pythonInterpreter} -c "import ${module}"`, (error, stdout, stderr) => {
                if (error) {
                    vscode.window.showInformationMessage(`${module} is not installed. Installing...`);
                    child_process.exec(`${pythonInterpreter} install ${module}`, (installError, installStdout, installStderr) => {
                        if (installError) {
                            vscode.window.showErrorMessage(`Failed to install ${module}: ${installStderr}`);
                        }
                        else {
                            vscode.window.showInformationMessage(`${module} installed successfully.`);
                        }
                    });
                }
            });
        });
    });
}
function createNewIoXPluginProject(context) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const workspaceFolder = yield vscode.window.showInputBox({
                prompt: 'Enter path for the new IoX Plugin project',
                value: vscode.workspace.workspaceFolders == undefined ? "type path here" : vscode.workspace.workspaceFolders[0].uri.fsPath
            });
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('Project creation cancelled.');
                return false;
            }
            const scriptPath = path.join(context.extensionPath, 'code', 'new_project.py');
            const pythonProcess = child_process.spawn('python3', [scriptPath, workspaceFolder, context.extensionPath]);
            pythonProcess.stdout.on('data', (data) => {
                console.log(`${data}`);
                vscode.window.showInformationMessage(`${data}`);
            });
            pythonProcess.stderr.on('data', (data) => {
                console.error(`${data}`);
                vscode.window.showErrorMessage(`${data}`);
            });
            pythonProcess.on('close', (code) => {
                if (code !== 0) {
                    console.log(`${code}`);
                    vscode.window.showErrorMessage(`${code}`);
                    return false;
                }
                else {
                    console.log('Generating IoX Plugin project completed successfully');
                    vscode.window.showInformationMessage('Generating IoX Plugin project completed successfully');
                }
            });
        }
        catch (error) {
            if (typeof error === "object" && error !== null && "message" in error) {
                const message = error.message;
                vscode.window.showErrorMessage(`Failed to create project: ${message}`);
            }
            else {
                vscode.window.showErrorMessage("Failed to create project due to an unknown error");
            }
            return false;
        }
        vscode.window.showInformationMessage('Generating IoX Plugin project completed successfully');
        return true;
    });
}
function generatePluginCode(context, fileUri) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            let workspaceFolder = vscode.workspace.workspaceFolders == undefined ? "type path here" : vscode.workspace.workspaceFolders[0].uri.fsPath;
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('Cannot find project directory');
                return false;
            }
            const scriptPath = path.join(context.extensionPath, 'code', 'plugin.py');
            const pythonProcess = child_process.spawn('python3', [scriptPath, workspaceFolder, fileUri.fsPath]);
            pythonProcess.stdout.on('data', (data) => {
                console.log(`${data}`);
                vscode.window.showInformationMessage(`${data}`);
            });
            pythonProcess.stderr.on('data', (data) => {
                console.error(`${data}`);
                vscode.window.showErrorMessage(`${data}`);
            });
            pythonProcess.on('close', (code) => {
                if (code !== 0) {
                    console.log(`IoX Plugin Code generation exited with code ${code}`);
                    vscode.window.showErrorMessage(`IoX Plugin Code generation exited with code ${code}`);
                    return false;
                }
                else {
                    console.log('IoX Plugin Code generation completed successfully');
                    vscode.window.showInformationMessage('IoX Plugin Code generation completed successfully');
                }
            });
        }
        catch (error) {
            if (typeof error === "object" && error !== null && "message" in error) {
                const message = error.message;
                vscode.window.showErrorMessage(`Failed to generated IoX Plugin Code: ${message}`);
            }
            else {
                vscode.window.showErrorMessage(`Failed to generated IoX Plugin Code due to an unknown error`);
            }
            return false;
        }
        vscode.window.showInformationMessage('IoX Plugin Code generation completed successfully');
        return true;
    });
}
function activate(context) {
    let python_dep = vscode.commands.registerCommand('extension.ensurePythonDependencies', () => __awaiter(this, void 0, void 0, function* () {
        checkAndInstallPythonModules();
    }));
    context.subscriptions.push(python_dep);
    checkAndInstallPythonModules();
    let createProject = vscode.commands.registerCommand('extension.createProject', () => __awaiter(this, void 0, void 0, function* () {
        let prc = yield createNewIoXPluginProject(context);
        if (prc.valueOf())
            context.subscriptions.push(createProject);
    }));
    let generateCode = vscode.commands.registerCommand('extension.generatePluginCode', (fileUri) => __awaiter(this, void 0, void 0, function* () {
        let prc = yield generatePluginCode(context, fileUri);
        if (prc.valueOf())
            context.subscriptions.push(generateCode);
    }));
}
exports.activate = activate;
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map