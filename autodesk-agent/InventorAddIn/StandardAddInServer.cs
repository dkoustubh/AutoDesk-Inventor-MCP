using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace InventorAIChatAddIn
{
    [Guid("E1A472E8-8956-4BC9-9A74-D72D1E4E81C5")]
    [ComVisible(true)]
    public class StandardAddInServer
    {
        private dynamic? m_inventorApplication;
        private dynamic? m_dockableWindow;
        private WebBrowser? m_webBrowser;
        private Form? m_hostForm;

        private const string SERVER_URL = "http://192.168.11.94:5173";

        public void Activate(object AddInSiteObject, bool FirstTime)
        {
            try
            {
                dynamic site = AddInSiteObject;
                m_inventorApplication = site.Application;

                // 1. Create Web Browser Host Control
                m_hostForm = new Form
                {
                    FormBorderStyle = FormBorderStyle.None,
                    TopLevel = false,
                    Visible = true
                };

                m_webBrowser = new WebBrowser
                {
                    Dock = DockStyle.Fill,
                    ScriptErrorsSuppressed = true,
                    Url = new Uri(SERVER_URL)
                };
                m_hostForm.Controls.Add(m_webBrowser);

                // 2. Create Autodesk Inventor Dockable Window
                dynamic uiMgr = m_inventorApplication.UserInterfaceManager;
                m_dockableWindow = uiMgr.DockableWindows.Add(
                    "{E1A472E8-8956-4BC9-9A74-D72D1E4E81C5}",
                    "InventorAIChatDockable",
                    "InventorAI Chat"
                );

                // 3. Embed Form into Dockable Window & Dock Right
                m_dockableWindow.AddChild(m_hostForm.Handle.ToInt32());
                m_dockableWindow.DockingState = 4; // kDockRight
                m_dockableWindow.Visible = true;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"InventorAI Chat AddIn notice: {ex.Message}", "InventorAI Chat");
            }
        }

        public void Deactivate()
        {
            try
            {
                if (m_dockableWindow != null)
                {
                    m_dockableWindow.Visible = false;
                    m_dockableWindow.Delete();
                    m_dockableWindow = null;
                }
                if (m_hostForm != null)
                {
                    m_hostForm.Dispose();
                    m_hostForm = null;
                }
                m_inventorApplication = null;
            }
            catch { }
            GC.Collect();
            GC.WaitForPendingFinalizers();
        }

        public void ExecuteCommand(int CommandID) { }

        public object? Automation => null;
    }
}
