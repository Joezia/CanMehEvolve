
Field::Field(const Field &field)
    : FieldBase(field)
    , profile(field.profile) // Removed std::move since field is const; copy is correct and avoids unnecessary overhead
    , profileIndex(field.profileIndex)
    , type(field.type)
    , isFieldExpanded(field.isFieldExpanded)
{
}
