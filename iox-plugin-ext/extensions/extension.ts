import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import * as child_process from 'child_process';

async function checkAndInstallPythonModules() {
  const pythonInterpreter = vscode.workspace.getConfiguration('python3').get<string>('pythonPath', 'pip3');

  const modules = ['astor'];  // Example modules
  modules.forEach(module => {
      child_process.exec(`${pythonInterpreter} -c "import ${module}"`, (error, stdout, stderr) => {
          if (error) {
              vscode.window.showInformationMessage(`${module} is not installed. Installing...`);
              child_process.exec(`${pythonInterpreter} install ${module}`, (installError, installStdout, installStderr) => {
                  if (installError) {
                      vscode.window.showErrorMessage(`Failed to install ${module}: ${installStderr}`);
                  } else {
                      vscode.window.showInformationMessage(`${module} installed successfully.`);
                  }
              });
          }
      });
  });
}

async function createNewIoXPluginProject(context: vscode.ExtensionContext) 
{
    try {
        const workspaceFolder = await vscode.window.showInputBox({
            prompt: 'Enter path for the new IoX Plugin project',
            value: vscode.workspace.workspaceFolders == undefined? "type path here": vscode.workspace.workspaceFolders[0].uri.fsPath
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
              } else {
                  console.log('Generating IoX Plugin project completed successfully');
                  vscode.window.showInformationMessage('Generating IoX Plugin project completed successfully');
              }
        });

    } catch (error: unknown) {
        if (typeof error === "object" && error !== null && "message" in error) {
            const message = (error as { message: string }).message;
            vscode.window.showErrorMessage(`Failed to create project: ${message}`);
        } else {
            vscode.window.showErrorMessage("Failed to create project due to an unknown error");
        }
        return false;
    }
    vscode.window.showInformationMessage('Generating IoX Plugin project completed successfully');
    return true;
}

async function generatePluginCode(context: vscode.ExtensionContext, fileUri: vscode.Uri) 
{
    try {
        let workspaceFolder = vscode.workspace.workspaceFolders == undefined? "type path here": vscode.workspace.workspaceFolders[0].uri.fsPath;

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
              } else {
                  console.log('IoX Plugin Code generation completed successfully');
                  vscode.window.showInformationMessage('IoX Plugin Code generation completed successfully');
              }
        });

    } catch (error: unknown) {
        if (typeof error === "object" && error !== null && "message" in error) {
            const message = (error as { message: string }).message;
            vscode.window.showErrorMessage(`Failed to generated IoX Plugin Code: ${message}`);
        } else {
            vscode.window.showErrorMessage(`Failed to generated IoX Plugin Code due to an unknown error`);
        }
        return false;
    }
    vscode.window.showInformationMessage('IoX Plugin Code generation completed successfully');
    return true;
}



export function activate(context: vscode.ExtensionContext) {

  let python_dep = vscode.commands.registerCommand('extension.ensurePythonDependencies', async () => {
    checkAndInstallPythonModules();
  });
  context.subscriptions.push(python_dep);
  checkAndInstallPythonModules();

  let createProject = vscode.commands.registerCommand('extension.createProject', async () => {
    let prc = await createNewIoXPluginProject(context);
    if (prc.valueOf())
      context.subscriptions.push(createProject)
  });

  let generateCode = vscode.commands.registerCommand('extension.generatePluginCode', async (fileUri: vscode.Uri)  => {
    let prc = await generatePluginCode(context, fileUri);
    if (prc.valueOf())
      context.subscriptions.push(generateCode)
  });

}

export function deactivate() {}
