import io.javalin.Javalin
import io.javalin.http.staticfiles.Location
import redis.clients.jedis.Jedis


const val STORAGE_PATH = "mount/storage"


class App(
    val javalin: Javalin,
    val userStorage: UserStorage,
    val sessionManager: SessionManager
)


fun main() {
    val userStorage = UserStorage("mount/users")
    val jedis = Jedis("redis", 6379)
    val sessionManager = SessionManager(jedis)
    val javalin = Javalin.create { config ->
        config.addStaticFiles("src/main/resources/static", Location.EXTERNAL)
    }.start(3687)
    App(javalin, userStorage, sessionManager).apply {
        addRegisterPageHandler()
        addLoginPageHandler()
        addLoginHandler()
        addRegisterHandler()
        addLogoutHandler()
        addMainHandler()
        addIndexHandler()
        addFilesHandler()
        addUploadFilesHandler()
    }
}
