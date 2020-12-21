using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CarpetRadar.Services.DataStorage;
using CarpetRadar.Services.IdentityServices;
using CarpetRadar.Services.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using NLog;

namespace CarpetRadar.Web2.Pages
{
    public class StatisticsModel : PageModel
    {
        public (string Login, string Company) UserInfo { get; set; }
        public IEnumerable<Flight> UserFlights { get; set; }
        public bool IsAuthenticated { get; set; }

        private readonly IAuthenticationService authenticationService;
        private readonly IDataStorage dataStorage;
        private readonly ILogger logger;

        public StatisticsModel(IAuthenticationService authenticationService, IDataStorage dataStorage, ILogger logger)
        {
            this.authenticationService = authenticationService;
            this.dataStorage = dataStorage;
            this.logger = logger;
        }

        public async Task<IActionResult> OnGet()
        {
            var userId = await authenticationService.ResolveUser(Request.Cookies["token"]);
            if (userId == null)
            {
                IsAuthenticated = false;
                return Page();
            }

            IsAuthenticated = true;
            UserInfo = await dataStorage.GetUserInfo(userId.Value);
            UserFlights = await dataStorage.GetUserFlights(userId.Value);
            return Page();
        }
    }
}
