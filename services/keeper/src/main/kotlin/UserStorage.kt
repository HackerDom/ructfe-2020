import java.io.File

class UserStorage(
    storagePath: String
) {
    private val storagePath = File(storagePath)

    init {
        if (!this.storagePath.exists()) {
            this.storagePath.mkdirs()
        }
    }

    fun exists(username: String) = storagePath.resolve(safeEscapeLogin(username)).exists()
    fun create(username: String, password: String) {
        storagePath.resolve(safeEscapeLogin(username)).writeBytes(stringHash(password))
    }

    fun isValid(username: String, password: String): Boolean {
        val safeUsername = safeEscapeLogin(username)
        if (!exists(safeUsername)) {
            return false
        }
        return storagePath.resolve(safeUsername).readBytes().contentEquals(stringHash(password))
    }
}
