Field::Field(const Field &field)
    : FieldBase()
    , profile(field.profile)
    , profileIndex(field.profileIndex)
    , type(field.type)
    , isFieldExpanded(field.isFieldExpanded)
{
    num = field.num;
    size = field.size;
    std::memcpy(value, field.value, size);
}
