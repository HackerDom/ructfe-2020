import io.javalin.Javalin
import kotlinx.html.*
import kotlinx.html.stream.appendHTML
import java.io.File
import java.nio.file.Path


const val STORAGE_PATH = "mount"


fun main(args: Array<String>) {
    val app = Javalin.create().start(8080)
    app.get("/*") { ctx ->
        val file = File(STORAGE_PATH).resolve(ctx.path().substring(1))
        println(file)
        if (!file.exists()) {
            ctx.result("Not found")
            return@get
        }

        if (file.isFile) {
            ctx.result(file.readBytes())
            return@get
        }

        if (file.isDirectory) {
            ctx.res.writer.appendHTML().html {
                body {
                    ul {
                        for (name in file.list()) {
                            li {
                                a(File(ctx.path()).resolve(name).toString()) {
                                    +name
                                }
                            }
                        }
                    }
                }
            }
            ctx.contentType("text/html")
        }
    }
    app.post("/upload") { ctx ->
        ctx.uploadedFiles("files").forEach { (contentType, content, name, extension) ->
            println(contentType)
            println(content)
            println(name)
            println(extension)
        }
    }
}
