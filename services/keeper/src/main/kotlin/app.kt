import jnr.ffi.Pointer
import redis.clients.jedis.Jedis
import ru.serce.jnrfuse.ErrorCodes
import ru.serce.jnrfuse.FuseFillDir
import ru.serce.jnrfuse.FuseStubFS
import ru.serce.jnrfuse.struct.FileStat
import ru.serce.jnrfuse.struct.FuseFileInfo
import ru.serce.jnrfuse.struct.FusePollhandle
import java.io.File
import kotlin.math.max
import kotlin.random.Random
import kotlin.system.exitProcess


const val APPEND_FLAG = 1024


class FSException(
    override val message: String
): Exception(message) {
    init {
        println("FS exception:")
        this.stackTrace.forEach {
            println(it)
        }
        exitProcess(1)
    }
}


sealed class IMEntity(
        val client: Jedis,
        val id: Int
) {
    companion object {
        fun fromId(client: Jedis, id: Int): IMEntity? {
            if (client["f$id"] != null) {
                return IMFile(client, id)
            }
            if (client["d$id"] != null) {
                return IMDir(client, id)
            }
            return null
        }
    }
}


class IMFile(
        client: Jedis,
        private var _data: ByteArray,
        id: Int
): IMEntity(client, id) {
    constructor(client: Jedis, data: ByteArray = ByteArray(0)) : this(client, data, genId()) {
        this.data = data
    }

    var data: ByteArray
        get() = _data
        set(value) {
            client["f$id".encodeToByteArray()] = value
        }

    fun write(data: ByteArray, offset: Int, size: Int, isAppend: Boolean) {
        val finalSize =
            if (isAppend) max(_data.size, offset + size)
            else offset + size
        val result = ByteArray(finalSize) {
            if (it in _data.indices) _data[it]
            else 0
        }
        println("result: ${result.decodeToString()}")
        for (index in data.indices) {
            result[index + offset] = data[index]
        }
        this.data = result
    }

    constructor(client: Jedis, id: Int) : this(client, dataById(client, id), id)

    val size: Int
        get() = _data.size

    override fun toString(): String {
        return "IMFile(id=$id)"
    }

    companion object {
        fun genId() = Random.nextInt()

        fun dataById(client: Jedis, id: Int) = client["f$id".encodeToByteArray()]
    }
}


class IMDir(
        client: Jedis,
        id: Int
) : IMEntity(client, id) {
    constructor(client: Jedis): this(client, genId()) {
        client["d$id"] = ""
    }

    operator fun set(name: String, entity: IMEntity) {
        val data = HashMap<String, IMEntity>()
        parseData()
            .forEach { pair ->
                pair.second?.let {
                    data[pair.first] = it
                }
            }

        data[name] = entity
        dumpData(data.toList())
    }

    private fun dumpData(data: List<Pair<String, IMEntity>>) {
        client["d$id"] = data.joinToString(",") {
            "${it.first}=${it.second.id}"
        }
    }

    private fun parseData() = client["d$id"]
        .split(",")
        .filterNot { it.isEmpty() }
        .map { it.split("=") }
        .map { it[0] to fromId(client, it[1].toInt()) }
        .mapNotNull { pair -> pair.second?.let { ent -> pair.first to ent } }

    operator fun get(name: String): IMEntity? {
        parseData().forEach { pair ->
            if (pair.first == name) {
                return pair.second
            }
        }
        return null
    }

    fun keys() = parseData().map { it.first }

    fun remove(name: String) {
        val data = parseData()
            .filter { it.first != name }
        dumpData(data)
    }

    override fun toString(): String {
        return "IMDir(id=$id)"
    }

    companion object {
        fun genId() = Random.nextInt()
    }
}


class RedisFSTree(
        private val client: Jedis
) {
    private val root = IMDir(client)

    init {
        mkdir("/dir")
        create("/dir/file")
        write("/dir/file", "Hello!".encodeToByteArray())
    }

    fun findEntity(path: String) = findEntity(splitPath(path), root)

    fun findEntity(path: List<String>, node: IMEntity, index: Int = 0, size: Int = path.size): IMEntity? {
        if (index == size) {
            return node
        }
        if (node is IMDir) {
            node[path[index]]?.let { next ->
                return findEntity(path, next, index + 1, size)
            }
        }
        return null
    }

    private fun splitPath(path: String): List<String> = path.trim('/').split("/").filterNot { it.isEmpty() }

    private fun extractPathEntity(path: String): Pair<IMDir, String>? {
        val splitted = splitPath(path)
        return findEntity(splitted, root, 0, splitted.size - 1)?.let {
            if (it is IMDir) {
                it to splitted[splitted.size - 1]
            } else null
        }
    }

    fun mkdir(path: String): Boolean {
        val (pathEntity, name) = extractPathEntity(path) ?: return true
        pathEntity[name] = IMDir(client)
        return false
    }

    fun rmdir(path: String): Boolean {
        val (pathEntity, name) = extractPathEntity(path) ?: return true
        pathEntity.remove(name)
        return false
    }

    fun create(path: String): Boolean {
        val (pathEntity, name) = extractPathEntity(path) ?: return true
        pathEntity[name] = IMFile(client)
        return false
    }

    fun unlink(path: String): Boolean {
        val (pathEntity, name) = extractPathEntity(path) ?: return true
        pathEntity.remove(name)
        return false
    }

    fun lsDir(path: String): List<String> {
        val dir = findEntity(path)
        if (dir is IMDir) {
            return dir.keys()
        }
        throw FSException("No such directory")
    }

    fun read(path: String) = ((findEntity(path) as? IMFile) ?: throw FSException("No such file")).data

    fun write(path: String, data: ByteArray, offset: Int = 0, size: Int = data.size, isAppend: Boolean = false) {
        ((findEntity(path) as? IMFile) ?: throw FSException("No such file")).write(data, offset, size, isAppend)
    }

    fun isDir(path: String) = findEntity(path) is IMDir
    fun isFile(path: String) = findEntity(path) is IMFile
    fun fileSize(path: String) = ((findEntity(path) as? IMFile) ?: throw FSException("No such file")).size
}


class MyFS(
        client: Jedis
): FuseStubFS() {
    private val fs = RedisFSTree(client)

    override fun readdir(path: String, buf: Pointer, filter: FuseFillDir, offset: Long, fi: FuseFileInfo): Int {
        synchronized(this) {
//        println("readdir $path")
            if (!fs.isDir(path)) {
                return -ErrorCodes.ENOTDIR()
            }

//        println("lsdir $path")
            fs.lsDir(path).forEach {
                filter.apply(buf, it, null, 0)
            }
            filter.apply(buf, ".", null, 0)
            filter.apply(buf, "..", null, 0)
        }
        return 0
    }

    override fun truncate(path: String?, size: Long): Int {
//        println("truncate $path")
        return 0
    }

    override fun getattr(path: String, stat: FileStat): Int {
//        println("getattr $path")
        if (fs.isDir(path)) {
//            println("$path is dir")
            stat.st_nlink.set(2)
            stat.st_mode.set(FileStat.S_IFDIR)
            return 0
        }
        if (fs.isFile(path)) {
//            println("$path is file, size=${fs.fileSize(path)}")
            stat.st_mode.set(FileStat.S_IFREG or FileStat.ALL_WRITE or FileStat.ALL_READ)
            stat.st_size.set(fs.fileSize(path))
            return 0
        }
        return -ErrorCodes.ENOENT()
    }

    override fun read(path: String, buf: Pointer, size: Long, offset: Long, fi: FuseFileInfo): Int {
        println("read: $path")
        if (!fs.isFile(path)) {
            return -ErrorCodes.ENOENT()
        }
        val data = fs.read(path)
        println("data: '${data.decodeToString()}', size: ${data.size}")
        buf.put(0, data, 0, data.size)
        return data.size
    }

    override fun write(path: String, buf: Pointer, size: Long, offset: Long, fi: FuseFileInfo): Int {
        val isAppend = fi.flags.get() and APPEND_FLAG != 0
        println("write: $path, offset=$offset, size=$size, isAppend=$isAppend")
        val bytesToWrite = ByteArray(size.toInt())
        buf.get(0, bytesToWrite, 0, size.toInt())
        fs.write(path, bytesToWrite, offset.toInt(), size.toInt(), isAppend)
        return bytesToWrite.size
    }

    override fun create(path: String, mode: Long, fi: FuseFileInfo): Int {
        fs.create(path)
        return 0
    }

    override fun mkdir(path: String, mode: Long): Int {
        if (fs.mkdir(path)) {
            return -ErrorCodes.ENOTDIR()
        }
        return 0
    }

    override fun rmdir(path: String): Int {
        println("rmdir: $path")
        if (fs.rmdir(path)) {
            return -ErrorCodes.ENOENT()
        }
        return 0
    }

    override fun unlink(path: String): Int {
        println("unlink: $path")
        if (fs.unlink(path)) {
            return -ErrorCodes.ENOENT()
        }
        return 0
    }

    override fun flush(path: String?, fi: FuseFileInfo?): Int {
        return 0
    }

    override fun poll(path: String?, fi: FuseFileInfo?, ph: FusePollhandle?, reventsp: Pointer?): Int {
        return 0
    }
}


fun main() {
    val jedis = Jedis("localhost", 6379)
    jedis.connect()
    val mountPath = File("mount").toPath()
    val myFS = MyFS(jedis)
    myFS.mount(mountPath, true, true)
    println("!")
}
