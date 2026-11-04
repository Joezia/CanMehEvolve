Field::Field(const Field &field)
    : FieldBase(field.fieldDefinition)
    , profile(field.profile)
    , profileIndex(field.profileIndex)
    , type(field.type)
    , isFieldExpanded(field.isFieldExpanded)
{
    values = field.values;
}
