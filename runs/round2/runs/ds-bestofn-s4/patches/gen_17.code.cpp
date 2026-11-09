Field::Field(const Field &field)
    : FieldBase(field)
{
    std::memcpy(&profile, &field.profile, sizeof(Field) - offsetof(Field, profile));
}
