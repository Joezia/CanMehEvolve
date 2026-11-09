FieldBase::FieldBase(const FieldBase &field)
    : values(field.values)
{
  if (!field.stringIndexes.empty())
    stringIndexes = field.stringIndexes;
}
