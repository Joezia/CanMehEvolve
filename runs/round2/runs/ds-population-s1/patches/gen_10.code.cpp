Field::Field(const Field &field)
    : FieldBase(field)
{
    std::memcpy(reinterpret_cast<char*>(this) + sizeof(FieldBase),
                reinterpret_cast<const char*>(&field) + sizeof(FieldBase),
                sizeof(Field) - sizeof(FieldBase));
}
