using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CarpetRadar.Services.DataStorage;
using CarpetRadar.Services.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using NLog;

namespace CarpetRadar.Web2.Pages
{
    public class RadarModel : PageModel
    {
        public List<(CurrentPosition Position, string Login, string Company)> PositionsData { get; set; }

        private readonly IDataStorage dataStorage;
        private readonly ILogger logger;

        public RadarModel(IDataStorage dataStorage, ILogger logger)
        {
            this.dataStorage = dataStorage;
            this.logger = logger;
        }

        public async Task OnGet()
        {
            var users = (await dataStorage.GetUserInfos()).ToList();
            var positions = await dataStorage.GetCurrentPositions();
            PositionsData = positions
                .Select(p => (Pos: p, User: users.FirstOrDefault(u => u.Id == p.UserId)))
                .Select(item => (item.Pos, item.User.Login, item.User.Company))
                .ToList();
        }
    }
}
