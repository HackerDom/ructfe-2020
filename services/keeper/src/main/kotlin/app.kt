import io.javalin.Javalin


const val STORAGE_PATH = "mount/storage"


class App(
    val javalin: Javalin,
    val userStorage: UserStorage,
    val sessionManager: SessionManager
)


fun main(args: Array<String>) {
    val userStorage = UserStorage("mount/users")
    val sessionManager = SessionManager("mount/sessions")

    val javalin = Javalin.create().start(8080)
    val app = App(javalin, userStorage, sessionManager).apply {
        addRegisterPageHandler()
        addLoginPageHandler()
        addLoginHandler()
        addMainHandler()
        addRegisterHandler()
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
