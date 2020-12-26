import io.javalin.Javalin
import io.javalin.http.staticfiles.Location
import redis.clients.jedis.JedisPool
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
    val chest = File("src/main/resources/static/chest.txt").readText()
    val jedisPool = JedisPool("redis", 6379)
    val sessionManager = SessionManager(jedisPool)
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
