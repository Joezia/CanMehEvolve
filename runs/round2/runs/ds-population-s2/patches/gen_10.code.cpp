Field::Field(const Field &field)
    : FieldBase(field)
{
    std::memcpy(static_cast<void*>(reinterpret_cast<char*>(this) + sizeof(FieldBase)),
                static_cast<const void*>(reinterpret_cast<const char*>(&field) + sizeof(FieldBase)),
                sizeof(Field) - sizeof(FieldBase));
}
