
Field::Field(const Field &field)
    : FieldBase(field)
{
    std::memcpy(&profile, &field.profile,
                reinterpret_cast<const char*>(&field.isFieldExpanded) + sizeof(field.isFieldExpanded)
                - reinterpret_cast<const char*>(&field.profile));
}
