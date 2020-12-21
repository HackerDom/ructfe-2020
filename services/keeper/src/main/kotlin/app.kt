import io.javalin.Javalin
import io.javalin.http.staticfiles.Location
import java.io.File


const val STORAGE_PATH = "mount/storage"


class App(
    val javalin: Javalin,
    val userStorage: UserStorage,
    val sessionManager: SessionManager
)


fun main(args: Array<String>) {
    val userStorage = UserStorage("mount/users")
    val sessionManager = SessionManager("mount/sessions")

    println(File("src/main/resources/static").exists())
//    return
    val javalin = Javalin.create { config ->
        config.addStaticFiles("src/main/resources/static", Location.EXTERNAL)
    }.start(8080)
    val app = App(javalin, userStorage, sessionManager).apply {
        addRegisterPageHandler()
        addLoginPageHandler()
        addLoginHandler()
        addRegisterHandler()
        addFilesHandler()
        addMainHandler()
    }

//    app.javalin.post("/upload") { ctx ->
//        ctx.uploadedFiles("files").forEach { (contentType, content, name, extension) ->
//            println(contentType)
//            println(content)
//            println(name)
//            println(extension)
//        }
//    }
}
