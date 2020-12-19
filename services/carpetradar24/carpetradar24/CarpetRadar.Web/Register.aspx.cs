using System;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Web;
using System.Web.UI;
using CarpetRadar.Services.IdentityServices;
using NLog;

namespace CarpetRadar.Web
{
    public partial class Register : Page
    {
        private readonly IRegistrationService registrationService;
        private readonly IAuthenticationService authenticationService;
        private readonly ILogger logger;

        public Register(IRegistrationService registrationService, IAuthenticationService authenticationService, ILogger logger)
        {
            this.registrationService = registrationService;
            this.authenticationService = authenticationService;
            this.logger = logger;
        }

        protected void Page_Load(object sender, EventArgs e)
        {
            cmdRegister.ServerClick += (o, ev) => cmdRegister_ServerClick(o, ev).GetAwaiter().GetResult();
        }

        private async Task<(bool IsRegistered, string Token)> RegisterUser(string userName, string companyName, string passWord)
        {
            if (userName == null || !Regex.IsMatch(userName, "\\w{3,15}"))
            {
                logger.Info("[RegisterUser] Input validation of userName failed.");
                return (false, null);
            }

            // Check for invalid passWord.
            // passWord must not be null and must be between 1 and 25 characters.
            if ((null == passWord) || (0 == passWord.Length) || (passWord.Length > 25))
            {
                logger.Info("[RegisterUser] Input validation of passWord failed.");
                return (false, null);
            }

            var userId = await registrationService.RegisterUser(userName, passWord, companyName);
            if (userId == null)
                return (false, null);

            string token = null;
            try
            {
                token = await authenticationService.AuthenticateAndGetToken(userName, passWord);
            }
            catch (Exception ex)
            {
                logger.Error(ex, "[RegisterUser] Exception ");
            }

            // If no password found, return false.
            if (token == null)
            {
                // You could write failed login attempts here to event log for additional security.
                return (false, null);
            }

            return (true, token);
        }

        private async Task cmdRegister_ServerClick(object _, EventArgs __)
        {
            var authResult = await RegisterUser(txtUserName.Value, txtCompanyName.Value, txtUserPass.Value);
            if (authResult.IsRegistered)
            {
                //var tkt = new FormsAuthenticationTicket(1, txtUserName.Value, DateTime.Now,
                //    DateTime.Now.AddMinutes(30), chkPersistCookie.Checked, "your custom data");
                //var cookie = FormsAuthentication.Encrypt(tkt);
                //var ck = new HttpCookie(FormsAuthentication.FormsCookieName, cookie);
                //if (chkPersistCookie.Checked)
                //    ck.Expires = tkt.Expiration;
                //ck.Path = FormsAuthentication.FormsCookiePath;

                Response.Cookies.Add(new HttpCookie("token", authResult.Token));
                var strRedirect = Request["ReturnUrl"] ?? "Default.aspx";
                Response.Redirect(strRedirect, false);
            }
            else
                Response.Redirect("Register.aspx", true);
        }
    }
}
