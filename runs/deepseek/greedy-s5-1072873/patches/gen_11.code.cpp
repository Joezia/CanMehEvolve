__attribute__((optimize("O3")))
FieldBase::FieldBase(const FieldBase &field)
    : values(field.values),
      stringIndexes(field.stringIndexes)
{
}
