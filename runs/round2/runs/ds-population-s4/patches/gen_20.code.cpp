Field::Field(const Field &field)
    : FieldBase(field)
    , profile(field.profile)
    , profileIndex(field.profileIndex)
{
    std::memcpy(&type, &field.type, sizeof(type) + sizeof(isFieldExpanded));
}
