using System;
using System.Net;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Web;
using System.Web.Security;
using System.Web.UI;
using CarpetRadar.Services.IdentityServices;
using NLog;

namespace CarpetRadar.Web
{
    public partial class Login : Page
    {
        private readonly IAuthenticationService authenticationService;
        private readonly ILogger logger;

        public Login(IAuthenticationService authenticationService, ILogger logger)
        {
            this.authenticationService = authenticationService;
            this.logger = logger;
        }

        protected void Page_Load(object sender, EventArgs e)
        {
            cmdLogin.ServerClick += (o, ev) => cmdLogin_ServerClick(o, ev).GetAwaiter().GetResult();
        }

        private async Task<(bool IsAuthenticated, string Token)> AuthenticateUser(string userName, string passWord)
        {
            if (userName == null || !Regex.IsMatch(userName, "\\w{3,15}"))
            {
                logger.Info("[AuthenticateUser] Input validation of userName failed.");
                return (false, null);
            }

            if ((null == passWord) || (0 == passWord.Length) || (passWord.Length > 25))
            {
                logger.Info("[AuthenticateUser] Input validation of passWord failed.");
                return (false, null);
            }

            string token = null;
            try
            {
                token = await authenticationService.AuthenticateAndGetToken(userName, passWord);
            }
            catch (Exception ex)
            {
                logger.Error(ex, "[AuthenticateUser] Exception ");
            }

            if (token == null)
            {
                // You could write failed login attempts here to event log for additional security.
                return (false, null);
            }

            return (true, token);
        }

        private async Task cmdLogin_ServerClick(object sender, EventArgs e)
        {
            var authResult = await AuthenticateUser(txtUserName.Value, txtUserPass.Value);
            if (authResult.IsAuthenticated)
            {
                var tkt = new FormsAuthenticationTicket(1, txtUserName.Value, DateTime.Now,
                    DateTime.Now.AddMinutes(30), chkPersistCookie.Checked, "your custom data");
                var cookie = FormsAuthentication.Encrypt(tkt);
                var ck = new HttpCookie(FormsAuthentication.FormsCookieName, cookie);
                if (chkPersistCookie.Checked)
                    ck.Expires = tkt.Expiration;
                ck.Path = FormsAuthentication.FormsCookiePath;

                Response.Cookies.Add(new HttpCookie("token", authResult.Token));
                var strRedirect = Request["ReturnUrl"] ?? "default.aspx";
                Response.Redirect(strRedirect, true);
            }
            else
            {
                Response.StatusCode = (int) HttpStatusCode.Unauthorized;
                Response.Redirect("login.aspx", true);
            }
        }
    }
}
