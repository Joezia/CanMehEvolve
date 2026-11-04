Field::Field(const Field &field)
    : FieldBase(field)
{
    std::memcpy(static_cast<void*>(&profile),
                static_cast<const void*>(&field.profile),
                sizeof(Field) - sizeof(FieldBase));
}
