
Field::Field(const Field &field)
    : FieldBase(field)
    , profile(std::move(field.profile))
    , profileIndex(field.profileIndex)
    , type(field.type)
    , isFieldExpanded(field.isFieldExpanded)
{
}
