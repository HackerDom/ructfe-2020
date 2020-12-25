using System;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using CarpetRadar.Services.DataStorage;
using NLog;

namespace CarpetRadar.Services.IdentityServices
{
    public interface IRegistrationService
    {
        Task<Guid?> RegisterUser(string login, string password, string companyName);
    }

    public class RegistrationService : IRegistrationService
    {
        private readonly IDataStorage dataStorage;
        private readonly ILogger log;

        public RegistrationService(IDataStorage dataStorage, ILogger log)
        {
            this.dataStorage = dataStorage;
            this.log = log;
        }

        public async Task<Guid?> RegisterUser(string login, string password, string companyName)
        {
            if (!Regex.IsMatch(login, "^\\w{3,15}$"))
                return null;

            var userId = Guid.NewGuid();
            var passwordHash = password.CalculateHash();

            try
            {
                await dataStorage.SaveUserInfo(login, userId, passwordHash, companyName);
                return userId;
            }
            catch (Exception e)
            {
                log.Error(e);
                return null;
            }
        }
    }
}
