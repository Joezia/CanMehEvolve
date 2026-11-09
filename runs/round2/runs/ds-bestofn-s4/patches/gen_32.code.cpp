Field::Field(const Field &field)
{
    std::memcpy(static_cast<void *>(this), static_cast<const void *>(&field), sizeof(Field));
}
