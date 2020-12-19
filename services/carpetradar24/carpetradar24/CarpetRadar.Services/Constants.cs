namespace CarpetRadar.Services
{
    public static class Constants
    {
        public const string KeySpace = "carpetradar";

        public static class ColumnFamily
        {
            public const string Users = "users";
            public const string Tokens = "tokens";
            public const string CarpetFlights = "carpetFlights";
            public const string CurrentPositions = "currentPositions";
        }
    }
}
