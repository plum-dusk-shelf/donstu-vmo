package models.schemas;

import java.util.Date;
import java.util.UUID;

public class Picture {
    public UUID id;
    public String filename;
    public int size;
    public Date created_at;

    public Picture(UUID id, String filename, int size, Date created_at) {
        this.id = id;
        this.filename = filename;
        this.size = size;
        this.created_at = created_at;
    }
}
