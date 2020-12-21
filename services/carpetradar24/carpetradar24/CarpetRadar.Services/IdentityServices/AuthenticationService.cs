using System;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using CarpetRadar.Services.DataStorage;

namespace CarpetRadar.Services.IdentityServices
{
    public interface IAuthenticationService
    {
        Task<Guid?> ResolveUser(string token);
        Task<string> AuthenticateAndGetToken(string login, string passwordHash);
    }

    public class AuthenticationService : IAuthenticationService
    {
        private readonly IDataStorage dataStorage;

        public AuthenticationService(IDataStorage dataStorage)
        {
            this.dataStorage = dataStorage;
        }

        public async Task<Guid?> ResolveUser(string token)
        {
            if (string.IsNullOrEmpty(token))
                return null;

            if (!Regex.IsMatch(token, "^\\w{32}$"))
                return null;

            var (userId, authTime) = await dataStorage.FindUser(token);

            if (userId == null || authTime == null)
                return null;

            if (DateTime.UtcNow - authTime.Value > TimeSpan.FromDays(1))
                return null;

            return userId;
        }

        public async Task<string> AuthenticateAndGetToken(string login, string password)
        {
            var passwordHash = password.CalculateHash();

            var result = await dataStorage.GetUserIdAndPasswordHash(login);
            if (result == null)
                return null;

            var (userId, realPasswordHash) = result.Value;
            if (passwordHash != realPasswordHash)
                return null;

            var token = Guid.NewGuid().ToString("N");
            await dataStorage.SetUserToken(userId, token);
            return token;
        }
    }
}
