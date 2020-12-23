using System;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Web;

namespace CarpetRadar.Services.IdentityServices
{
    public static class IdentityExtensions
    {
        public static async Task<Guid?> ResolveUser(this IAuthenticationService authenticationService, HttpCookie tokenCookie)
        {
            if (tokenCookie?.Value == null)
                return null;

            var token = tokenCookie.Value;

            if (!Regex.IsMatch(token, "^\\w{32}$"))
                return null;

            return await authenticationService.ResolveUser(token);
        }

        public static long CalculateHash(this string password)
        {
            var passwordBytes = Encoding.ASCII.GetBytes(password);
            var components = MD5.Create().ComputeHash(passwordBytes).Select((a, i) => a * (long) Math.Pow(256, i));

            long passwordHash = 0;
            foreach (long c in components)
            {
                passwordHash += c;
            }

            return passwordHash;
        }
    }
}
