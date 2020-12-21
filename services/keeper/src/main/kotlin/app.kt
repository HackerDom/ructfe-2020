import io.javalin.Javalin
import io.javalin.http.staticfiles.Location


const val STORAGE_PATH = "mount/storage"


class App(
    val javalin: Javalin,
    val userStorage: UserStorage,
    val sessionManager: SessionManager
)


fun main(args: Array<String>) {
    val userStorage = UserStorage("mount/users")
    val sessionManager = SessionManager("mount/sessions")
    val javalin = Javalin.create { config ->
        config.addStaticFiles("src/main/resources/static", Location.EXTERNAL)
    }.start(3687)
    val app = App(javalin, userStorage, sessionManager).apply {
        addRegisterPageHandler()
        addLoginPageHandler()
        addLoginHandler()
        addRegisterHandler()
        addMainHandler()
        addIndexHandler()
        addFilesHandler()
        addUploadFilesHandler()
    }
}
