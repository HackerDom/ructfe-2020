using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using CarpetRadar.Services.IdentityServices;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using NLog;

namespace CarpetRadar.Web2.Pages
{
    public class LoginOrRegisterModel : PageModel
    {
        private readonly IRegistrationService registrationService;
        private readonly IAuthenticationService authenticationService;
        private readonly ILogger logger;

        public LoginOrRegisterModel(IRegistrationService registrationService, IAuthenticationService authenticationService, ILogger logger)
        {
            this.registrationService = registrationService;
            this.authenticationService = authenticationService;
            this.logger = logger;
        }

        private List<string> errors = new List<string>();
        public List<string> RegisterErrors { get; set; }
        public List<string> LoginErrors { get; set; }

        public async Task<IActionResult> OnPostRegister(string userName, string password, string company)
        {
            var result = await RegisterAction(userName, password, company);
            RegisterErrors = errors;
            return result;
        }

        public async Task<IActionResult> OnPostLogin(string userName, string password, string company)
        {
            var result = await LoginAction(userName, password);
            LoginErrors = errors;
            return result;
        }

        private async Task<IActionResult> RegisterAction(string userName, string password, string company)
        {
            if (!ValidateRegistration(userName, password, company))
                return Page();

            var isRegistered = await RegisterUser(userName, password, company);
            if (!isRegistered)
            {
                return Page();
            }

            var isAuthenticated = await AuthenticateUser(userName, password);
            if (!isAuthenticated)
            {
                return Page();
            }

            return RedirectToPage("/Statistics");
        }

        private async Task<IActionResult> LoginAction(string userName, string password)
        {
            if (!ValidateLogin(userName, password))
            {
                return Page();
            }

            var isAuthenticated = await AuthenticateUser(userName, password);
            if (!isAuthenticated)
            {
                return Page();
            }

            return RedirectToPage("/Statistics");
        }

        private async Task<bool> RegisterUser(string userName, string password, string company)
        {
            try
            {
                var userId = await registrationService.RegisterUser(userName, password, company);
                if (userId == null)
                {
                    errors.Add("Wrong registration information");
                    return false;
                }

                return true;
            }
            catch (Exception ex)
            {
                logger.Error(ex, "[RegisterUser] Exception ");
                errors.Add("Something went wrong, try to repeat request later");
                return false;
            }
        }

        private async Task<bool> AuthenticateUser(string userName, string password)
        {
            try
            {
                var token = await authenticationService.AuthenticateAndGetToken(userName, password);
                if (token == null)
                {
                    errors.Add("Wrong username or password");
                    return false;
                }

                var cookieOptions = new CookieOptions
                {
                    Expires = DateTime.UtcNow.AddDays(3)
                };
                Response.Cookies.Append("token", token, cookieOptions);
                return true;
            }
            catch (Exception ex)
            {
                logger.Error(ex, "[AuthenticateUser] Exception ");
                errors.Add("Something went wrong, try to repeat request later");
                return false;
            }
        }

        private bool ValidateRegistration(string userName, string password, string company) => ValidateUserName(userName) & ValidatePassword(password) & ValidateCompany(company);

        private bool ValidateLogin(string userName, string password) => ValidateUserName(userName) & ValidatePassword(password);

        private bool ValidateUserName(string userName)
        {
            if (userName != null && Regex.IsMatch(userName, "\\w{3,15}"))
                return true;

            errors.Add("Incorrect username");
            return false;
        }

        private bool ValidatePassword(string password)
        {
            if (password != null && Regex.IsMatch(password, "\\S{3,25}"))
                return true;

            errors.Add("Incorrect password");
            return false;
        }

        private bool ValidateCompany(string company)
        {
            if (company != null)
                return true;

            errors.Add("Incorrect company name");
            return false;
        }
    }
}
