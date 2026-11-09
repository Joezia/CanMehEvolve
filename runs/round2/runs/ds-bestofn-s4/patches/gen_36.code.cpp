Field::Field(const Field &field)
    : FieldBase(field)
{
    std::memcpy(static_cast<FieldBase*>(this) + 1,
                static_cast<const FieldBase*>(&field) + 1,
                sizeof(Field) - sizeof(FieldBase));
}
