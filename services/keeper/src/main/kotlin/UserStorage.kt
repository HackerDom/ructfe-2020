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

    fun exists(username: String) = storagePath.resolve(username).exists()
    fun create(username: String, password: String) {
        storagePath.resolve(username).writeBytes(stringHash(password))
    }

    fun isValid(username: String, password: String): Boolean {
        if (!exists(username)) {
            return false
        }
        return storagePath.resolve(username).readBytes().contentEquals(stringHash(password))
    }
}
