import io.javalin.Javalin
import io.javalin.http.staticfiles.Location
import redis.clients.jedis.Jedis
import java.io.File


const val STORAGE_PATH = "mount/storage"


class App(
    val javalin: Javalin,
    val userStorage: UserStorage,
    val sessionManager: SessionManager,
    val chest: String
)


fun main() {
    val userStorage = UserStorage("mount/users")
    val jedis = Jedis("redis", 6379)
    val chest = File("src/main/resources/static/chest.txt").readText()
    val sessionManager = SessionManager(jedis)
    val javalin = Javalin.create { config ->
        config.addStaticFiles("src/main/resources/static", Location.EXTERNAL)
    }.start(3687)
    App(javalin, userStorage, sessionManager, chest).apply {
        addRegisterPageHandler()
        addLoginPageHandler()
        addLoginHandler()
        addRegisterHandler()
        addLogoutHandler()
        addMainHandler()
        addIndexHandler()
        addFilesHandler()
        addUploadFilesHandler()
        addCoolChestHandler()
        addIsLoginExistsHandler()
        addCheckPairHandler()
    }
}
